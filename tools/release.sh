#!/usr/bin/env bash

function die {
  echo "error: $@"
  exit 1
}

while [[ $# -gt 0 ]]
do
  key="$1"
  case $key in
    --pypi-key)
      export TWINE_PASSWORD="$2"
      shift 2
    ;;
    --release-mode)
      release_mode="$2"
      shift 2
    ;;
    *)
      echo "unknown argument: ${key}"
      exit 1
    ;;
  esac
done

[[ ! -z "${TWINE_PASSWORD}" ]] || die "please provide a valid pypi API key with --pypi-key"

repository=
if [[ "${release_mode}" == "prod" ]]
then
  repository=pypi
elif [[ "${release_mode}" == "test" ]]
then
  repository=testpypi
else
  echo "missing or invalid release mode (${release_mode})"
  exit 1
fi

echo "packaging quickforex"

python setup.py sdist bdist_wheel

echo "releasing quickforex to ${repository}"

export TWINE_USERNAME=__token__
twine upload --repository ${repository} dist/*
