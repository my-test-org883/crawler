#!/usr/bin/env python3

import subprocess

from application.collector.scripts.utils import image_digest


def main():
    IMAGE_URL = "ghcr.io/example/image"
    latest_version = git_latest_tag(IMAGE_URL)

    BASE_SHA = image_digest(f"{IMAGE_URL}:py312-app-{latest_version}")
    BUILD_SHA = image_digest(f"{IMAGE_URL}:py312-build-{latest_version}")
    APK_SHA = image_digest(f"{IMAGE_URL}:py312-apk-{latest_version}")

    print(f"Latest version: {latest_version}")
    print(f"Base image digest: {BASE_SHA}")
    print(f"Build image digest: {BUILD_SHA}")
    print(f"APK image digest: {APK_SHA}")


def git_latest_tag(repo_url):
    """Given a repository URL get the latest semver tag."""
    args = [
        "bash",
        "-ec",
        """
        set -o pipefail
        git ls-remote --tags "$0" | cut -d/ -f3 | sort -r --version-sort | head -n1
        """,
        repo_url,
    ]

    return subprocess.check_output(args, cwd="/tmp").decode().strip()


if __name__ == "__main__":
    main()
