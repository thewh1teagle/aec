from hatchling.builders.hooks.plugin.interface import BuildHookInterface
import os


class CustomBuildHook(BuildHookInterface):
    def initialize(self, version, build_data):
        build_data["pure_python"] = False
        tag = os.getenv("WHEEL_TAG")
        if tag:
            # py3-none-linux_x86_64
            # py3-none-win_amd64
            # py3-none-macosx_11_0_arm64
            # py3-none-macosx_10_12_x86_64
            # PYTHON_TAG='py3-none-linux_x86_64' uv build
            build_data["tag"] = tag
        else:
            build_data["infer_tag"] = True
