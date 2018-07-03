resource "aws_vpc" "kubernaut" {
  cidr_block           = "10.10.0.0/16"

  enable_dns_support   = true
  enable_dns_hostnames = true

  tags = "${merge(map("Name", var.cluster_name, "kubernaut.io/cluster/name", var.cluster_name, format("kubernetes.io/cluster/%v", var.cluster_name), "owned"), var.tags)}"
}

resource "aws_internet_gateway" "main" {
  vpc_id = "${aws_vpc.kubernaut.id}"

  tags = "${merge(map("Name", var.cluster_name, "kubernaut.io/cluster/name", var.cluster_name, format("kubernetes.io/cluster/%v", var.cluster_name), "owned"), var.tags)}"
}

resource "aws_subnet" "kubernaut" {
  cidr_block = "10.10.0.0/20"
  vpc_id     = "${aws_vpc.kubernaut.id}"
  tags = "${merge(map("Name", var.cluster_name, "kubernaut.io/cluster/name", var.cluster_name, format("kubernetes.io/cluster/%v", var.cluster_name), "owned"), var.tags)}"
}

resource "aws_route" "external" {
  route_table_id         = "${aws_vpc.kubernaut.default_route_table_id}"
  destination_cidr_block = "0.0.0.0/0"
  gateway_id             = "${aws_internet_gateway.main.id}"
}

resource "aws_route_table_association" "kubernaut" {
  subnet_id      = "${aws_subnet.kubernaut.id}"
  route_table_id = "${aws_vpc.kubernaut.default_route_table_id}"
}

resource "aws_security_group" "kubernaut" {
  vpc_id      = "${aws_vpc.kubernaut.id}"
  name_prefix = "kubernaut-"
  description = "main security group"

  tags = "${merge(map("Name", var.cluster_name, "kubernaut.io/cluster/name", var.cluster_name, format("kubernetes.io/cluster/%v", var.cluster_name), "owned"), var.tags)}"

  lifecycle {
    create_before_destroy = true
  }
}

resource "aws_security_group_rule" "nodeport" {
  cidr_blocks       = ["0.0.0.0/0"]
  from_port         = 30000
  to_port           = 32767
  protocol          = "all"
  security_group_id = "${aws_security_group.kubernaut.id}"
  type              = "ingress"
}

resource "aws_security_group_rule" "ssh" {
  cidr_blocks       = ["0.0.0.0/0"]
  from_port         = 22
  to_port           = 22
  protocol          = "tcp"
  security_group_id = "${aws_security_group.kubernaut.id}"
  type              = "ingress"
}

resource "aws_security_group_rule" "api_server" {
  cidr_blocks       = ["0.0.0.0/0"]
  from_port         = 6443
  to_port           = 6443
  protocol          = "tcp"
  security_group_id = "${aws_security_group.kubernaut.id}"
  type              = "ingress"
}

resource "aws_security_group_rule" "egress" {
  cidr_blocks       = ["0.0.0.0/0"]
  from_port         = 1
  to_port           = 65535
  protocol          = "all"
  security_group_id = "${aws_security_group.kubernaut.id}"
  type              = "egress"
}
