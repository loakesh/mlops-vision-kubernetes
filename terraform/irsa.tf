# This module creates the IAM role and maps it to the Kubernetes ServiceAccount via OIDC
module "irsa_role" {
  source  = "terraform-aws-modules/iam/aws//modules/iam-role-for-service-accounts-eks"
  version = "~> 5.30"

  role_name = "cv-pipeline-irsa-role"

  # Map this IAM role to our specific Kubernetes namespace and service account
  oidc_providers = {
    ex = {
      provider_arn               = module.eks.oidc_provider_arn
      namespace_service_accounts = ["default:cv-pipeline-sa"]
    }
  }

  # We can reuse the policy we already created for Jenkins, 
  # or attach specific managed policies
  role_policy_arns = {
    policy = aws_iam_policy.jenkins_policy.arn
  }
}
