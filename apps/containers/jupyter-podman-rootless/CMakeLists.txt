cmake_minimum_required(VERSION 3.15...3.31)

project(
  ${SKBUILD_PROJECT_NAME}
  VERSION ${SKBUILD_PROJECT_VERSION}
  LANGUAGES NONE
)

# scikit-build-core handles Python package installation via wheel.packages
