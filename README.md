# ECS on Fargate with IPv6 VPC

IPv6を有効にしたVPC上でECSサービスを動作させるサンプルです。
ECSサービスで動作するアプリケーションは [amazon-ecs-sample](https://hub.docker.com/r/amazon/amazon-ecs-sample) です。

## 開発方法

CDK Pythonプロジェクトです。以下の手順にしたがって開発してください。

1. `source .venv/bin/activate` でvenvを有効化する
2. `cdk diff` で作成されるリソースを確認する
3. `cdk deploy` でリソースを作成する

デプロイが成功したらAWSコンソールを開いて、ECSサービスで動作しているタスクの「ネットワーキング」タブを開いてください。
タスクに割り当てられたIPv6アドレスをコピーして、HTTPでアクセスできた動作確認に成功です。
