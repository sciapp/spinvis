#!/bin/bash

install_dependencies () {
    # Fall back to a `mktemp` variant with `-t` if using older osx systems
    TMP_DEPENDENCY_DIR="$(mktemp -d 2>/dev/null || mktemp -d -t 'tmp')" || return 1
    PIP_ROOT="${TMP_DEPENDENCY_DIR}/pip_root"
    PIP_BIN="${PIP_ROOT}/usr/local/bin"
    PIP_SITE_PACKAGES="${PIP_ROOT}/Library/Python/2.7/site-packages"
    export PATH="${PIP_BIN}:/usr/bin:/bin:/usr/sbin:/sbin"
    export PYTHONPATH="${PIP_SITE_PACKAGES}"
    local PIP_URL="https://bootstrap.pypa.io/get-pip.py"

    pushd "${TMP_DEPENDENCY_DIR}" && \
    curl -O -L "${PIP_URL}" && \
    chmod +x ./get-pip.py && \
    ./get-pip.py --root "${PIP_ROOT}" --ignore-installed && \
    pip install --root "${PIP_ROOT}" --ignore-installed shallow-appify && \
    popd
}

create_dmg () {
    local VERSION_STRING return_code

    mkdir -p app && \
    cp -r ../../spinvis app/ && \
    cat <<-EOF > app/main.py
		#!/usr/bin/env python3

		from spinvis.spinVis_gui import main

		if __name__ == "__main__":
		    main()
	EOF
    VERSION_STRING="$(cd ../../spinvis && python -c 'import _version; print _version.__version__')" && \
    PATH="/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin" \
    "${PIP_BIN}/shallow-appify" -d ./app/ \
                                -i ../../icon.png \
                                -g sciapp \
                                -v "${VERSION_STRING}" \
                                -e PATH \
                                -o SpinVis.dmg ./app/main.py
    return_code="$?"
    rm -rf app

    return "${return_code}"
}

cleanup () {
    rm -rf "${TMP_DEPENDENCY_DIR}"
}

main () {
    local return_code

    install_dependencies && \
    create_dmg
    return_code="$?"
    cleanup

    return "${return_code}"
}

main "$@"
