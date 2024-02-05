# ECS on Fargate with IPv6 VPC

IPv6を有効にしたVPC上でECSサービスを動作させるサンプルです。
ECSサービスで動作するアプリケーションは [amazon-ecs-sample](https://hub.docker.com/r/amazon/amazon-ecs-sample) です。

## インフラ構成

IPv6アドレスのみが付与されたパブリックサブネット上でECSサービスが動作しています。
[amazon/amazon-ecs-sample](https://hub.docker.com/r/amazon/amazon-ecs-sample)をアプリケーションとして動かしています。
ロギングのためにFluent Bitを動作させ、ログをS3バケットに保存します。

![](./ipv6vpc.drawio.svg)

### 注意点

AWSにはIPv6に対応していないサービスがあります。

* ECRはIPv6に対応していないため、dockerhubからイメージをpullします。
* CloudWatch LogsはIPv6に対応していないため、Fluent BitとS3をログの保存に利用します。

## 開発方法

CDK Pythonプロジェクトです。以下の手順にしたがって開発してください。

1. `source .venv/bin/activate` でvenvを有効化する
2. `cdk diff` で作成されるリソースを確認する
3. `cdk deploy` でリソースを作成する

デプロイが成功したらAWSコンソールを開いて、ECSサービスで動作しているタスクの「ネットワーキング」タブを開いてください。
タスクに割り当てられたIPv6アドレスをコピーして、HTTPでアクセスできた動作確認に成功です。
