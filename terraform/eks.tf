module "eks" {
  source  = "terraform-aws-modules/eks/aws"
  version = "~> 20.0"

  cluster_name    = "cv-pipeline-cluster"
  cluster_version = "1.30"

  # Cluster endpoint access
  cluster_endpoint_public_access  = true

  vpc_id                   = module.vpc.vpc_id
  subnet_ids               = module.vpc.private_subnets
  control_plane_subnet_ids = module.vpc.private_subnets

  # OIDC provider is REQUIRED for IAM Roles for Service Accounts (IRSA)
  enable_irsa = true

  # Default node group settings
  eks_managed_node_group_defaults = {
    instance_types = ["t3.medium"]
  }

  eks_managed_node_groups = {
    standard_nodes = {
      min_size     = 1
      max_size     = 3
      desired_size = 2
    }
  }

  # Add your current admin user so you can interact with the cluster
  enable_cluster_creator_admin_permissions = true

  # Grant the Jenkins EC2 Server admin access to deploy to Kubernetes
  access_entries = {
    jenkins_server = {
      kubernetes_groups = []
      principal_arn     = aws_iam_role.jenkins_role.arn

      policy_associations = {
        cluster_admin = {
          policy_arn = "arn:aws:eks::aws:cluster-access-policy/AmazonEKSClusterAdminPolicy"
          access_scope = {
            type = "cluster"
          }
        }
      }
    }
  }
}
