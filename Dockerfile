FROM hugomods/hugo:go-git-0.144.0 AS builder

WORKDIR /app

ADD ../ hugo

RUN cd hugo; \
    hugo -v --gc --minify

# RUN git clone https://github.com/smallersoup/envoy-handbook envoy-handbook; \
#     cd envoy-handbook; \
#     hugo -v --gc --minify

RUN git clone https://github.com/smallersoup/jstc

FROM fholzer/nginx-brotli:latest

LABEL org.opencontainers.image.source https://github.com/smallersoup/blog

COPY --from=builder /app/hugo/public /usr/share/nginx/html
# COPY --from=builder /app/envoy-handbook/public /usr/share/nginx/html/envoy-handbook
COPY --from=builder /app/jstc /usr/share/nginx/html/jstc