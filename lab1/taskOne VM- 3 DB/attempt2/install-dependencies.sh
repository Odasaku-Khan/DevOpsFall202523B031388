app-get update

apt-get install -y ca-certificates curl gnupg git

install -m 0755 -d /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | gpg --dearmor -o /etc/apt/keyrings/docker.gpg
chmod a+r /etc/apt/keyrings/docker.gpg

echo \
  "deb [arch="$(dpkg --print-architecture)" signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu \
  "$(. /etc/os-release && echo "$VERSION_CODENAME")" stable" | \
  tee /etc/apt/sources.list.d/docker.list > /dev/null

apt-get update
apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin

usermod -aG docker vagrant

if [ ! -d "/home/vagrant/terramino-go/.git" ]; then
  cd /home/vagrant
  rm -rf terramino-go
  git clone https://github.com/hashicorp-education/terramino-go.git
  cd terramino-go
  git checkout containerized
fi

cat > /usr/local/bin/reload-terramino << 'EOF'
#!/bin/bash
cd /home/vagrant/terramino-go
docker compose down
docker compose build --no-cache
docker compose up -d
EOF

chmod +x /usr/local/bin/reload-terramino

echo 'alias play="docker compose -f /home/vagrant/terramino-go/docker-compose.yml exec -it backend ./terramino-cli"' >> /home/vagrant/.bashrc
echo 'alias reload="sudo /usr/local/bin/reload-terramino"' >> /home/vagrant/.bashrc

echo "source /home/vagrant/.bashrc" >> /home/vagrant/.bash_profile


