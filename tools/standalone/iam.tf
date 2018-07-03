data "template_file" "kubernaut_policy" {
  template = "${var.iam_policy}"
  vars { }
}

resource "aws_iam_policy" "kubernaut_policy" {
  name_prefix = "kubernaut-"
  path        = "/kubernaut/${var.cluster_name}/"
  policy      = "${data.template_file.kubernaut_policy.rendered}"
}

resource "aws_iam_role" "kubernaut_role" {
  name_prefix = "kubernaut-"
  path               = "/kubernaut/${var.cluster_name}/"
  assume_role_policy = "${var.iam_role}"

  lifecycle {
    create_before_destroy = true
  }
}

resource "aws_iam_policy_attachment" "kubernaut-attach" {
  name       = "iam-attach-${var.cluster_name}"
  roles      = ["${aws_iam_role.kubernaut_role.name}"]
  policy_arn = "${aws_iam_policy.kubernaut_policy.arn}"
}

resource "aws_iam_instance_profile" "kubernaut_profile" {
  name_prefix = "kubernaut-"
  path = "/kubernaut/${var.cluster_name}/"
  role = "${aws_iam_role.kubernaut_role.name}"

  lifecycle {
    create_before_destroy = true
  }
}
