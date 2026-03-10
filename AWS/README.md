
# Nginx Media Server Setup for AWS

This guide explains how to install and configure **nginx on Ubuntu (AWS EC2)** to expose two media endpoints:

- **Public media** (no auth)  
- **Private media** (separate port, app-controlled access via mobile app)
---

Purpose of this documentation is to replicate setup across multiple AWS instances at ease.

## Requirements

- Ubuntu 24.04 (on AWS EC2)
- SSH access to the server
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

## 2. Create media directories (one for public access and one for authenticated users)
```
sudo mkdir -p /srv/media/public
sudo mkdir -p /srv/media/private
```

## 3. Configure nginx server
```
sudo nano /etc/nginx/sites-available/media
```
```
# Public endpoint (HTTP 8080)
server {
    listen 8080;
    server_name _;

    location / {
        alias /srv/media/public/;
        autoindex on;
        autoindex_exact_size off;
        autoindex_localtime on;
    }
}

# Private endpoint (HTTP 8081)
server {
    listen 8081;
    server_name _;

    location / {
        alias /srv/media/private/;
        autoindex on;
        autoindex_exact_size off;
        autoindex_localtime on;
    }
}

```
#### Enable
```
sudo ln -s /etc/nginx/sites-available/media /etc/nginx/sites-enabled/media
```

#### Test and reload nginx
```
sudo nginx -t
sudo systemctl reload nginx
```

## Note to self or whoever is reading this, make sure you set up elastic IP, otherwise everytime AWS restarts it will assign random public IP.

# Secure Media Server with HTTPS, App only Access, and Android Client

This project sets up a secure media server on AWS using **Nginx**, **HTTPS (self-signed certificate)**, and **app-only access control**, with an **Android app** as the trusted client.

The final result:
- Media is served over HTTPS instead of HTTP
- Browsers are blocked from accessing **private** media
- Only the Android app can access private content
- The app trusts a self-signed certificate embedded inside it
- Biometric auth allows access inside the app
  
---

## Architecture Overview

- Ports **8080 / 8081** were removed (was for http endpoint test)
- Only **80 → 443 redirect** and **443 HTTPS** remain
- Self-signed certificate is used
- Web browser access to **private** media blocked
- Only Authenticated user via app can access **private** media
---


