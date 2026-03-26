#!/bin/bash
# PHASE 2 : HARDENING VPS - Ocean Sentinel V3.0 MAS
# Agent DevOps - Cascade AI
# Date: 26 mars 2026

set -e  # Exit on error

echo "=========================================="
echo "PHASE 2 : HARDENING VPS SÉCURISATION"
echo "=========================================="
echo ""

# ÉTAPE 1 : Mise à jour système
echo "[1/6] Mise à jour système..."
apt update -y
apt upgrade -y
apt autoremove -y
echo "✅ Système mis à jour"
echo ""

# ÉTAPE 2 : Installation paquets de base
echo "[2/6] Installation paquets de base..."
apt install -y ufw fail2ban
echo "✅ UFW et Fail2ban installés"
echo ""

# ÉTAPE 3 : Création utilisateur sentinelle
echo "[3/6] Création utilisateur sentinelle..."
if id "sentinelle" &>/dev/null; then
    echo "⚠️  Utilisateur sentinelle existe déjà"
else
    useradd -m -s /bin/bash sentinelle
    usermod -aG sudo sentinelle
    echo "✅ Utilisateur sentinelle créé et ajouté au groupe sudo"
fi
echo ""

# ÉTAPE 4 : Configuration clé SSH pour sentinelle
echo "[4/6] Configuration clé SSH..."
mkdir -p /home/sentinelle/.ssh
chmod 700 /home/sentinelle/.ssh

# Copier la clé autorisée de root vers sentinelle (si existe)
if [ -f /root/.ssh/authorized_keys ]; then
    cp /root/.ssh/authorized_keys /home/sentinelle/.ssh/authorized_keys
    chmod 600 /home/sentinelle/.ssh/authorized_keys
    chown -R sentinelle:sentinelle /home/sentinelle/.ssh
    echo "✅ Clé SSH copiée pour sentinelle"
else
    echo "⚠️  Aucune clé SSH root trouvée - configuration manuelle requise"
fi
echo ""

# ÉTAPE 5 : Configuration SSH (port 61189)
echo "[5/6] Configuration SSH port 61189..."
cp /etc/ssh/sshd_config /etc/ssh/sshd_config.backup

# Modifier port SSH
sed -i 's/^#Port 22/Port 61189/' /etc/ssh/sshd_config
sed -i 's/^Port 22/Port 61189/' /etc/ssh/sshd_config

# Désactiver authentification par mot de passe
sed -i 's/^#PasswordAuthentication yes/PasswordAuthentication no/' /etc/ssh/sshd_config
sed -i 's/^PasswordAuthentication yes/PasswordAuthentication no/' /etc/ssh/sshd_config

# Désactiver root login
sed -i 's/^#PermitRootLogin yes/PermitRootLogin no/' /etc/ssh/sshd_config
sed -i 's/^PermitRootLogin yes/PermitRootLogin no/' /etc/ssh/sshd_config

echo "✅ SSH configuré (port 61189, password auth désactivé)"
echo ""

# ÉTAPE 6 : Configuration Firewall UFW
echo "[6/6] Configuration Firewall UFW..."
ufw default deny incoming
ufw default allow outgoing
ufw allow 61189/tcp comment 'SSH personnalisé'
ufw allow 80/tcp comment 'HTTP'
ufw allow 443/tcp comment 'HTTPS'
ufw --force enable
echo "✅ Firewall UFW activé"
echo ""

echo "=========================================="
echo "⚠️  ACTIONS MANUELLES REQUISES"
echo "=========================================="
echo ""
echo "1. FIREWALL HOSTINGER hPanel :"
echo "   - Aller sur hPanel > VPS > Sécurité > Pare-feu"
echo "   - Autoriser port TCP 61189 (SSH)"
echo "   - Autoriser port TCP 80 (HTTP)"
echo "   - Autoriser port TCP 443 (HTTPS)"
echo ""
echo "2. REDÉMARRAGE SSH :"
echo "   systemctl restart sshd"
echo ""
echo "3. TEST CONNEXION (depuis autre terminal) :"
echo "   ssh -p 61189 sentinelle@76.13.43.3"
echo ""
echo "⚠️  NE PAS FERMER CETTE SESSION SSH AVANT TEST RÉUSSI !"
echo ""
echo "=========================================="
echo "PHASE 2 TERMINÉE"
echo "=========================================="
