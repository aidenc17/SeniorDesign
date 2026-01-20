
# Nginx Media Server Setup for AWS

This guide explains how to install and configure **nginx on Ubuntu (AWS EC2)** to expose two media endpoints:

- **Public media** (no auth)  
- **Private media** (separate port, app-controlled access via mobile app)
- TBD
---

Purpose of this documentation is to replicate setup across multiple AWS instances at ease.

## Requirements

- Ubuntu 20.04+ (tested on AWS EC2)
- SSH access to the server
- Ports **8080** and **8081** allowed in AWS Security Group
- nginx installed as root / sudo

---

## 1. Install nginx

```
sudo apt update
sudo apt install -y nginx
```

#### Enable and start nginx
```
sudo systemctl enable nginx
sudo systemctl start nginx
```

#### Verify Nginx
```
nginx -v
```
