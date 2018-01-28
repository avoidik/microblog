#!/usr/bin/env bash

export DEBIAN_FRONTEND=noninteractive
export LC_ALL="en_US.UTF-8"
export LC_CTYPE="en_US.UTF-8"

echo "en_US.UTF-8 UTF-8" > /var/lib/locales/supported.d/en
DEBCONF_NONINTERACTIVE_SEEN=true dpkg-reconfigure locales

sed -i "s/[#]*PasswordAuthentication yes/PasswordAuthentication no/g" /etc/ssh/sshd_config
sed -i "s/UsePAM yes/UsePAM no/g" /etc/ssh/sshd_config
service ssh restart

echo 'DPkg::Post-Invoke { "rm -f /var/cache/apt/archives/*.deb /var/cache/apt/archives/partial/*.deb /var/cache/apt/*.bin || true"; };' > /etc/apt/apt.conf.d/apt-clean
echo 'APT::Update::Post-Invoke { "rm -f /var/cache/apt/archives/*.deb /var/cache/apt/archives/partial/*.deb /var/cache/apt/*.bin || true"; };' >> /etc/apt/apt.conf.d/apt-clean
echo 'Dir::Cache::pkgcache ""; Dir::Cache::srcpkgcache "";' >> /etc/apt/apt.conf.d/apt-clean

apt-get -y update
apt-get -y upgrade
apt-get -y install git-core ufw
apt-get -y install python3 python3-venv python3-dev python3-pip python3-setuptools

DB_ROOT=$(python3 -c "import uuid; print(uuid.uuid4().hex)")
debconf-set-selections <<< "mysql-server mysql-server/root_password password ${DB_ROOT}"
debconf-set-selections <<< "mysql-server mysql-server/root_password_again password ${DB_ROOT}"
apt-get -y install mysql-server postfix supervisor nginx redis-server apt-transport-https

echo "deb https://artifacts.elastic.co/packages/6.x/apt stable main" | tee /etc/apt/sources.list.d/es.list
wget -qO - https://artifacts.elastic.co/GPG-KEY-elasticsearch | apt-key add -
apt-get -y update
apt-get -y install openjdk-8-jre-headless elasticsearch

systemctl daemon-reload
systemctl restart elasticsearch
systemctl enable elasticsearch.service
systemctl start elasticsearch.service

if [[ ! -d "/opt/microblog" ]]; then
  mkdir -p /opt/microblog
  cd /opt/microblog
  git clone https://github.com/avoidik/microblog .
else
  cd /opt/microblog
fi
pip3 install -U pip setuptools wheel
python3 -m venv venv
source venv/bin/activate
pip3 install -U pip setuptools wheel
pip3 install -r requirements.txt

SECRET_KEY=$(python3 -c "import uuid; print(uuid.uuid4().hex)")
DB_PASS=$(python3 -c "import uuid; print(uuid.uuid4().hex)")
tee ".env" > /dev/null <<EOF
SECRET_KEY=${SECRET_KEY}
MAIL_SERVER=localhost
MAIL_PORT=25
DATABASE_URL=mysql+pymysql://microblog:${DB_PASS}@localhost:3306/microblog
ELASTICSEARCH_URL=http://localhost:9200
EOF

mysql -u root -p${DB_ROOT} -e "create database microblog character set utf8 collate utf8_bin;"
mysql -u root -p${DB_ROOT} -e "create user 'microblog'@'localhost' identified by '${DB_PASS}';"
mysql -u root -p${DB_ROOT} -e "grant all privileges on microblog.* to 'microblog'@'localhost';"
mysql -u root -p${DB_ROOT} -e "flush privileges;"

mkdir certs
openssl req -new -newkey rsa:2048 -days 365 -nodes -x509 -keyout certs/key.pem -out certs/cert.pem \
    -subj "/C=GB/ST=London/L=London/O=Global Security/OU=IT Department/CN=selfsigned.com" > /dev/null 2>&1

cp -a /automated/microblog /etc/nginx/sites-enabled/microblog
cp -a /automated/microblog.conf /etc/supervisor/conf.d/microblog.conf
cp -a /automated/worker.conf /etc/supervisor/conf.d/worker.conf
rm -f /etc/nginx/sites-enabled/default

ufw allow ssh
ufw allow http
ufw allow 443/tcp
ufw --force enable
ufw status

export FLASK_APP="microblog.py"
flask translate compile
flask db upgrade
flask seed --no-destructive

chown -R vagrant:vagrant /opt/microblog

echo "export FLASK_APP=\"microblog.py\"" >> /home/vagrant/.profile
echo "export LC_ALL=C.UTF-8" >> /home/vagrant/.profile
echo "export LANG=C.UTF-8" >> /home/vagrant/.profile

supervisorctl reload
service nginx reload
