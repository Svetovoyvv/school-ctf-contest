FROM mcr.microsoft.com/dotnet/sdk:8.0 AS build

WORKDIR /src
COPY app/ .

RUN chmod +x build.sh
ENTRYPOINT ["./build.sh"]
