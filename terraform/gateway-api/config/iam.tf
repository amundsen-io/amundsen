data "aws_caller_identity" "current" {}

locals {
  acctid = data.aws_caller_identity.current.account_id
}

resource "aws_iam_role" "execution_role" {
  name = "${var.namespace}_iam_for_lambdaAPIgw"

  assume_role_policy = <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Action": "sts:AssumeRole",
      "Principal": {
        "Service": [
          "lambda.amazonaws.com"
        ]
      },
      "Effect": "Allow",
      "Sid": ""
    }
  ]
}
EOF
}

data "aws_iam_policy_document" "execution_role" {
  statement {
    sid = "CreateCloudWatchLogGroups"
    actions = [
      "logs:CreateLogGroup",
    ]
    effect = "Allow"
    resources = [
      "arn:aws:logs:us-*:${local.acctid}:*"
    ]
  }
  statement {
    sid = "WriteCloudWatchLogs"
    actions = [
      "logs:CreateLogGroup",
      "logs:CreateLogStream",
      "logs:PutLogEvents"
    ]
    effect = "Allow"
    resources = [
      "arn:aws:logs:*:${local.acctid}:log-group:/aws/lambda/*:*"
    ]
  }
}

resource "aws_iam_policy" "execution_role" {
  name   = "${var.namespace}-lambdaAPIgwPolicy"
  path   = "/"
  policy = data.aws_iam_policy_document.execution_role.json
}

resource "aws_iam_role_policy_attachment" "execution_role" {
  role       = aws_iam_role.execution_role.name
  policy_arn = aws_iam_policy.execution_role.arn
}
