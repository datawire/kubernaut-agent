variable "region" {
  description = "AWS region to run the standalone kubernaut vm"
  default     = "us-east-1"
}

variable "bootstrap_repo" {
  description = "Accessible HTTPS of a bootstrap bundle"
  default     = ""
}

variable "bootstrap_bundle" {
  description = "Name of a bundle located under the bootstrap directory within the bootstrap repository"
  default     = ""
}

variable "cluster_name" {
  description = "Name of the Kubernaut cluster"
}

variable "tags" {
  description = "Tags added to the Kubernaut cluster infrastructure"
  type        = "map"
  default     = {}
}

variable "iam_role" {
  description = "IAM role configuration for the kubernaut instance"
  default = <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Action": "sts:AssumeRole",
      "Effect": "Allow",
      "Principal": {
        "Service": "ec2.amazonaws.com"
      }
    }
  ]
}
EOF
}

variable "iam_policy" {
  description = "IAM policy configuration for the kubernaut instance"
  default = <<EOF
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Action": [
                "ec2:*",
                "elasticloadbalancing:*"
                ],
            "Effect": "Allow",
            "Resource": "*"
        }
    ]
}
EOF
}

variable "instance_type" {
  description = "The size of the EC2 virtual machine"
  default     = "m3.medium"
}

variable "instance_spot_price" {
  description  = "The max price to pay for a spot instance reservation"
  type         = "map"
  default      = {
    "m3.medium" = "0.10"
    "m4.large"  = "0.10"
  }
}

variable "image_id" {
  description = "The ID of the Amazon Machine Image to use"
}

variable "ssh_public_key" {
  description = "Path to desired SSH public key to associate with the Kubernaut instance"
  default     = "insecure_rsa.pub"
}