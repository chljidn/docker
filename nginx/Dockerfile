FROM nginx:latest

COPY nginx.conf /etc/nginx/nginx.conf
COPY nginx-g.conf /etc/nginx/sites-enabled/
COPY dist /var/www/html/

EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
