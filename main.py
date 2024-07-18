import json
import os
import shutil
import subprocess
import traceback
from datetime import timedelta, datetime
from time import sleep

import docker.client
from tabulate import tabulate

from db import get_db_session
from db_models.docker_stats_db_model import DockerStatsDbModel

DOCKER_BASE_URL = os.environ["DOCKER_BASE_URL"]
SAMPLE_INTERVAL = os.environ.get("SAMPLE_INTERVAL") or 30                   # 30 seconds
DATA_RETENTION = os.environ.get("DATA_RETENTION") or 60 * 60 * 24 * 7 * 4   # 4 weeks


def calculate_memory_usage(container_stats):
    memory_stats = container_stats["memory_stats"]
    # Memory usage in bytes
    memory_usage_bytes = memory_stats["usage"]
    # Convert bytes to megabytes
    memory_usage_mb = memory_usage_bytes / (1024 * 1024)
    return memory_usage_mb


def calculate_cpu_usage(container_stats):
    cpu_stats = container_stats["cpu_stats"]
    precpu_stats = container_stats["precpu_stats"]

    # Total CPU Usage
    total_cpu_usage = cpu_stats["cpu_usage"]["total_usage"]
    previous_total_cpu_usage = precpu_stats["cpu_usage"]["total_usage"]
    # System CPU Usage
    system_cpu_usage = cpu_stats["system_cpu_usage"]

    # Calculate CPU Usage percentage
    cpu_delta = total_cpu_usage - previous_total_cpu_usage
    system_delta = system_cpu_usage - precpu_stats["system_cpu_usage"]

    cpu_percent = (cpu_delta / system_delta) * 100
    return cpu_percent


def get_disk_space_stats(folder):
    total, used, free = shutil.disk_usage(folder)
    return {
        "total": total,
        "used": used,
        "free": free,
        "percent": (used / total) * 100
    }


def tick(cli):
    stats = get_stats(cli)
    store_stats_in_mysql(stats)
    enforce_data_retention(cli)


def main():
    cli = docker.DockerClient(base_url=DOCKER_BASE_URL)
    while True:
        try:
            tick(cli)
        except:
            traceback.print_exc()

        sleep(SAMPLE_INTERVAL)


def store_stats_in_mysql(stats):
    print("Storing stats in MySQL")
    print()
    print()

    with get_db_session() as db_session:
        for stat in stats:
            if "cpu_usage" in stat:
                db_session.add(DockerStatsDbModel(
                    container_id=stat["container_id"],
                    container_name=stat["container_name"],
                    stat_name="cpu_usage",
                    stat_value=stat["cpu_usage"],
                    timestamp=datetime.utcnow()
                ))

            if "memory_usage" in stat:
                db_session.add(DockerStatsDbModel(
                    container_id=stat["container_id"],
                    container_name=stat["container_name"],
                    stat_name="memory_usage",
                    stat_value=stat["memory_usage"],
                    timestamp=datetime.utcnow()
                ))

            if "disk_usage" in stat:
                db_session.add(DockerStatsDbModel(
                    container_id=stat["container_id"],
                    container_name=stat["container_name"],
                    stat_name="disk_usage",
                    stat_value=stat["disk_usage"],
                    timestamp=datetime.utcnow()
                ))

        db_session.commit()

    print("Done")
    print()


def enforce_data_retention(cli):
    print("Enforcing data retention")
    with get_db_session() as db_session:
        db_session.query(DockerStatsDbModel).filter(
            DockerStatsDbModel.timestamp < (datetime.utcnow() - timedelta(seconds=DATA_RETENTION))
        ).delete()
        db_session.commit()
    print("Done")
    print()


def get_stats(cli):
    ret = []

    for container in cli.containers.list():
        stats = container.stats(stream=False)

        ret.append({
            "container_id": container.id,
            "container_name": container.name,
            "cpu_usage": calculate_cpu_usage(stats),
            "memory_usage": calculate_memory_usage(stats),
        })

    for key, folder in os.environ.items():
        if key == "TRACK_DISK_SPACE":
            name_for_stat = "main"
        elif key.startswith("TRACK_DISK_SPACE_"):
            name_for_stat = key[len("TRACK_DISK_SPACE_"):].lower().replace("_", " ")
        else:
            continue

        disk_stats = get_disk_space_stats(folder)
        ret.append({
            "container_id": "host_os",
            "container_name": name_for_stat,
            "disk_usage": disk_stats["percent"]
        })

    return ret


if __name__ == "__main__":
    main()
