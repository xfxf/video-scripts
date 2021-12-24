# packer {
#   required_plugins {
#     amazon = {
#       # version = ">= 0.0.1"
#       # source = "github.com/hashicorp/amazon"
#     }
#   }
# }

variable "instance_profile" {
  type = string
}

source "amazon-ebs" "main" {
  ami_name             = "packer jibri {{timestamp}}"
  instance_type        = "t3.small"
  region               = "ap-southeast-2"
  source_ami           = "ami-0bf8b986de7e3c7ce"
  ssh_username         = "ubuntu"
  ssh_interface        = "session_manager"
  communicator         = "ssh"
  iam_instance_profile = var.instance_profile
}

build {
  name = "jibri"

  sources = [
    "source.amazon-ebs.main"
  ]

  provisioner "shell" {
    scripts = fileset(".", "scripts/{wait,step1}.sh")
    execute_command = "sudo -S sh -c '{{ .Vars }} {{ .Path }}'"
  }

  provisioner "shell" {
    expect_disconnect = true
    inline = ["sudo reboot"]
    pause_after  = "10s"
  }

  provisioner "shell" {
      scripts = fileset(".", "scripts/{wait,step2}.sh")
      execute_command = "sudo -S sh -c '{{ .Vars }} {{ .Path }}'"
  }

  post-processor "shell-local" {
      inline = ["echo Hello World from ${source.type}.${source.name}"]
  }
}