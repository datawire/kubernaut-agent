output instance_id {
  value = "${aws_spot_instance_request.kubernaut.spot_instance_id}"
}

output instance_public_ip {
  value = "${aws_spot_instance_request.kubernaut.public_ip}"
}

output instance_public_dns {
  value = "${aws_spot_instance_request.kubernaut.public_dns}"
}

output instance_private_ip {
  value = "${aws_spot_instance_request.kubernaut.private_ip}"
}

output instance_private_dns {
  value = "${aws_spot_instance_request.kubernaut.private_dns}"
}