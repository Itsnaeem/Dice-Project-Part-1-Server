resource "aws_instance" "server" {
  ami           = "ami-0a91cd140a1fc148a" # Ubuntu AMI for us-east-2
  instance_type = "t2.micro"
  subnet_id     = "subnet-0513fd176fd782647" #  subnet
  vpc_security_group_ids = ["sg-0ed89c4f337f33716"] # Default VPC security group

  tags = {
    Name = "ServerInstance"
  }
}
