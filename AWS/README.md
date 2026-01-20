
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
- Ports **8080** and **8081** allowed in AWS Security Group (can be any port of your choosing)
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

## 4. AWS Security Group configuration
