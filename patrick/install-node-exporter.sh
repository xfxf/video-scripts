#!/usr/bin/env bash

useradd --no-create-home --shell /bin/false node_exporter

mkdir /opt/node_exporter

cd /opt/node_exporter

wget https://github.com/prometheus/node_exporter/releases/download/v1.8.2/node_exporter-1.8.2.linux-amd64.tar.gz

tar xvf node_exporter-1.8.2.linux-amd64.tar.gz --strip-components=1 -C .

chown -R node_exporter:node_exporter /opt/node_exporter

echo "[Unit]" > /etc/systemd/system/node_exporter.service
echo "Description=Node Exporter" >> /etc/systemd/system/node_exporter.service
echo "Wants=network-online.target" >> /etc/systemd/system/node_exporter.service
echo "After=network-online.target" >> /etc/systemd/system/node_exporter.service
echo "" >> /etc/systemd/system/node_exporter.service
echo "[Service]" >> /etc/systemd/system/node_exporter.service
echo "User=node_exporter" >> /etc/systemd/system/node_exporter.service
echo "Group=node_exporter" >> /etc/systemd/system/node_exporter.service
echo "Type=simple" >> /etc/systemd/system/node_exporter.service
echo "ExecStart=/opt/node_exporter/node_exporter --collector.systemd" >> /etc/systemd/system/node_exporter.service
echo "" >> /etc/systemd/system/node_exporter.service
echo "[Install]" >> /etc/systemd/system/node_exporter.service
echo "WantedBy=multi-user.target" >> /etc/systemd/system/node_exporter.service

systemctl daemon-reload
systemctl start node_exporter
systemctl enable node_exporter

journalctl -f --unit node_exporter

