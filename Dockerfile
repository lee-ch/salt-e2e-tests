FROM centos:7
LABEL maintainer="Lee Christensen"

# install SaltStack
RUN yum install https://repo.saltstack.com/yum/redhat/salt-repo-latest-2.el7.noarch.rpm -y \
    && yum clean expire-cache \
    && yum install -y \
        git \
        salt-minion \
        vim

# add minion's configuration modules
ADD conf/minion.d/* /etc/salt/minion.d/

# add top level states
ADD srv/salt /srv/salt
ADD srv/salt/* /srv/salt/

# add top level pillar
ADD srv/pillar /srv/pillar

# add salt state tests
RUN mkdir -p /srv/tests
ADD srv/tests/* /srv/tests/
ADD staterun.py /srv/tests/

# create formulas' directory
RUN mkdir -p /srv/formulas
