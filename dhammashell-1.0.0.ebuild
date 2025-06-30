# Copyright 2025 Gentoo Authors
# Distributed under the terms of the GNU General Public License v2

EAPI=8

PYTHON_COMPAT=( python3_13 )
DISTUTILS_USE_PEP517=standalone
inherit distutils-r1

DESCRIPTION="A brief description of the Python package"
HOMEPAGE="https://github.com/yoursw/dhammashell"
# https://github.com/yoursw/DhammaShell/archive/refs/heads/main.tar.gz
SRC_URI="https://github.com/yoursw/${PN}/archive/v${PV}.tar.gz -> ${P}.tar.gz"

LICENSE="AGPLv3"
SLOT="0"
KEYWORDS="~amd64"

DEPEND=""
RDEPEND="${DEPEND}"
BDEPEND="
	dev-python/setuptools[${PYTHON_USEDEP}]
	dev-python/wheel[${PYTHON_USEDEP}]
	test? (
		dev-python/pytest[${PYTHON_USEDEP}]
	)
"

distutils_enable_tests pytest

src_prepare() {
	default
	# Handle different build system configurations
	if [[ -f pyproject.toml ]]; then
		if grep -q 'build-backend = "setuptools' pyproject.toml; then
			DISTUTILS_USE_PEP517=setuptools
		elif grep -q 'build-backend = "poetry' pyproject.toml; then
			DISTUTILS_USE_PEP517=poetry
		fi
	elif [[ -f setup.py ]]; then
		DISTUTILS_USE_PEP517=setuptools
	fi
}

python_configure_all() {
	# Handle requirements.txt if present
	if [[ -f requirements.txt ]]; then
		einfo "Processing requirements.txt"
		# Convert requirements.txt to proper RDEPEND format
		# This would need manual verification
		sed -e 's/==.*//' -e 's/>=.*/ /' requirements.txt
	fi
}
