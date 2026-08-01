FROM php:8.2-cli-alpine

# Install system packages & build tools
RUN apk add --no-cache \
    postgresql-dev \
    libzip-dev \
    zip \
    unzip \
    git \
    bash

# Install PHP extensions
RUN docker-php-ext-install pdo_pgsql zip pcntl bcmath sockets

# Install redis extension
RUN apk add --no-cache --virtual .build-deps $PHPIZE_DEPS \
    && pecl install redis \
    && docker-php-ext-enable redis \
    && apk del .build-deps

# Install Composer
COPY --from=composer:latest /usr/bin/composer /usr/bin/composer

WORKDIR /var/www/html

EXPOSE 8000
EXPOSE 8080
