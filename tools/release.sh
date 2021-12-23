#!/usr/bin/env bash
set -e

SCRIPT_DIR="$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"

PYPI_REPO=${PYPI_REPO:-testpypi}

if [[ "${TWINE_PASSWORD}" == ":prompt" ]]
then
  echo -n "Twine password: "
  read -s TWINE_PASSWORD
  echo
fi

if [[ -z "${TWINE_USERNAME}" ]] || [[ -z "${TWINE_PASSWORD}" ]]
then
  echo "error: TWINE_USERNAME or TWINE_PASSWORD env variables are missing, aborting"
  exit 1
fi

commit_sha=$(git rev-parse HEAD)
commit_version=$(git tag --points-at HEAD  | sed 's/^.//')

if [[ -z "${commit_version}" ]]
then
  echo "error: this commit is not tagged with a version, aborting"
  exit 1
fi

package_version=$(python3 setup.py --version)

if [[ "${commit_version}" != "${package_version}" ]]
then
  echo "error: commit version (v${commit_version:-?.?.?}) is not the same as package version (${package_version}), aborting"
  exit 1
fi

echo "releasing quickforex v${package_version} from commit ${commit_sha}"

echo "creating quickforex v${package_version} package"

${SCRIPT_DIR}/package.sh

echo "publishing package to ${PYPI_REPO}"

python3 -m twine upload --repository "${PYPI_REPO}" dist/*

echo "all done"
