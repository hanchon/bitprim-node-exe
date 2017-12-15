import os
from conan.packager import ConanMultiPackager
import copy

if __name__ == "__main__":
    builder = ConanMultiPackager(username="bitprim", channel="stable",
                                 remotes="https://api.bintray.com/conan/bitprim/bitprim",
                                 archs=["x86_64"])

    # builder.add_common_builds(shared_option_name="bitprim-node:shared")
    builder.add_common_builds()

    filtered_builds = []
    for settings, options, env_vars, build_requires in builder.builds:
        if settings["build_type"] == "Release" \
                and (not "compiler.runtime" in settings or not settings["compiler.runtime"] == "MT"):

            env_vars["BITPRIM_BUILD_NUMBER"] = os.getenv('BITPRIM_BUILD_NUMBER', '-')
                
            opt1 = copy.deepcopy(options)
            opt2 = copy.deepcopy(options)

            opt1["bitprim-node-exe:with_rpc"] = "True"
            opt2["bitprim-node-exe:with_rpc"] = "False"

            filtered_builds.append([settings, opt1, env_vars, build_requires])
            filtered_builds.append([settings, opt2, env_vars, build_requires])

    builder.builds = filtered_builds
    builder.run()
