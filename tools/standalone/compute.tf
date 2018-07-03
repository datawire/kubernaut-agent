provider "aws" {
  region = "${var.region}"
}

resource "aws_key_pair" "kubernaut" {
  key_name_prefix = "kubernaut-${var.cluster_name}-"
  public_key      = "${file(pathexpand(var.ssh_public_key))}"
}

data "template_file" "bootstrap_vars" {
  template = "${file("${path.module}/bootstrap.vars")}"

  vars {
    bootstrap_repo   = "${var.bootstrap_repo}"
    bootstrap_bundle = "${var.bootstrap_bundle}"
  }
}

data "template_file" "cloudinit_config" {
  template = "${file("${path.module}/cloud-init-config.yaml")}"

  vars {
    bootstrap_vars = "${base64gzip(data.template_file.bootstrap_vars.rendered)}"
  }
}

data "template_cloudinit_config" "kubernaut_cloudinit" {
  gzip          = true
  base64_encode = true

  part {
    filename     = "cloud-init-config.yaml"
    content_type = "text/cloud-config"
    content      = "${data.template_file.cloudinit_config.rendered}"
  }

  part {
    filename     = "bootstrap.sh"
    content_type = "text/x-shellscript"
    content      = "${file("${path.module}/shim.sh")}"
  }
}

resource "aws_spot_instance_request" "kubernaut" {
  ami                         = "${var.image_id}"
  associate_public_ip_address = true
  iam_instance_profile        = "${aws_iam_instance_profile.kubernaut_profile.name}"
  instance_type               = "${var.instance_type}"
  subnet_id                   = "${aws_subnet.kubernaut.id}"
  user_data                   = "${data.template_cloudinit_config.kubernaut_cloudinit.rendered}"
  key_name                    = "${aws_key_pair.kubernaut.id}"
  monitoring                  = false
  spot_price                  = "${lookup(var.instance_spot_price, var.instance_type, "0.05")}"
  vpc_security_group_ids      = ["${aws_security_group.kubernaut.id}"]
  wait_for_fulfillment        = true

  root_block_device {
    volume_type           = "gp2"
    volume_size           = "20"
    delete_on_termination = true
  }

  tags = "${merge(map("Name", var.cluster_name, "kubernaut.io/cluster/name", var.cluster_name), var.tags)}"
}