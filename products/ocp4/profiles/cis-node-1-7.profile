---
documentation_complete: true

title: 'CIS Red Hat OpenShift Container Platform 4 Benchmark'

platform: ocp4-node

metadata:
    SMEs:
        - rhmdnd
        - Vincent056
        - yuumasato
    version: 1.7.0

description: |-
    This profile defines a baseline that aligns to the Center for Internet Security®
    Red Hat OpenShift Container Platform 4 Benchmark™, V1.7.

    This profile includes Center for Internet Security®
    Red Hat OpenShift Container Platform 4 CIS Benchmarks™ content.

    Note that this part of the profile is meant to run on the Operating System that
    Red Hat OpenShift Container Platform 4 runs on top of.

    This profile is applicable to OpenShift versions 4.12 and greater.

filter_rules: '"ocp4-node" in platform or "ocp4-master-node" in platform or "ocp4-node-on-sdn" in platform
    or "ocp4-node-on-ovn" in platform'

selections:
    - cis_ocp_1_4_0:all
