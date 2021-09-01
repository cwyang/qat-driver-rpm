#/bin/bash
set -e
if [ "$kver" == "" ]; then
    echo 'Usage:'
    echo '  docker run -it -v/usr/src:/usr/src -v/lib/modules:/lib/modules -v/tmp:/tmp -e"kver=[kernel_version]" rpmbuild:latest'
    exit 1
fi
rpmbuild -ba --define "kver ${kver}" qat.spec
cp -f rpm/*.rpm /tmp
echo "OK: We've built the following files on /tmp:"
for i in rpm/*.rpm; do
    echo ${i##rpm/}
done
