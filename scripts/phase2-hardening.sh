#!/bin/bash
set -e
apt update -y && apt upgrade -y && apt autoremove -y
apt install -y ufw fail2ban git curl htop
if ! id "sentinelle" &>/dev/null; then
    useradd -m -s /bin/bash sentinelle
    usermod -aG sudo sentinelle
    echo "sentinelle:bJ#X796c@GSH1&j45YHJ(SgQ80EHnO@QI4528" | chpasswd
fi
mkdir -p /home/sentinelle/.ssh
chmod 700 /home/sentinelle/.ssh
if [ -f /root/.ssh/authorized_keys ]; then
    cp /root/.ssh/authorized_keys /home/sentinelle/.ssh/authorized_keys
    chmod 600 /home/sentinelle/.ssh/authorized_keys
    chown -R sentinelle:sentinelle /home/sentinelle/.ssh
fi
cp /etc/ssh/sshd_config /etc/ssh/sshd_config.backup.$(date +%Y%m%d)
if ! grep -q "^Port 61189" /etc/ssh/sshd_config; then
    echo "Port 61189" >> /etc/ssh/sshd_config
fi
sed -i 's/^#PasswordAuthentication yes/PasswordAuthentication no/' /etc/ssh/sshd_config
sed -i 's/^PasswordAuthentication yes/PasswordAuthentication no/' /etc/ssh/sshd_config
sed -i 's/^#PermitRootLogin yes/PermitRootLogin yes/' /etc/ssh/sshd_config
sed -i 's/^PermitRootLogin prohibit-password/PermitRootLogin yes/' /etc/ssh/sshd_config
systemctl restart sshd
echo "PHASE 2 TERMINEE - SSH ecoute sur port 61189"
