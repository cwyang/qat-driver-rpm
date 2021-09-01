FROM rpmbuild/centos7
MAINTAINER Chul-Woong Yang <cwyang@gmail.com>
USER root
RUN yum install -y centos-release-scl
RUN yum install -y kernel-devel libudev-devel devtoolset-9

USER builder
WORKDIR /home/builder
COPY qat.spec run.sh ./
COPY qat_contig_mem.tar.gz qat1.7.l.4.11.0-00001.tar.gz uname_r.patch ./rpm/

CMD ["scl", "enable", "devtoolset-9", "./run.sh"]