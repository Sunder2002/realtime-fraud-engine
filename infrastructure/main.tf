provider "aws" {
  region = "us-east-1"
}

resource "aws_instance" "fraud_engine_server" {
  ami           = "ami-0c55b159cbfafe1f0" # Ubuntu
  instance_type = "t3.medium"

  tags = {
    Name = "FraudDetectionEngine-Prod"
    Project = "RealTimeStreaming"
  }
}