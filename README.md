# AWS Helper

A utility that lets you use AWS SSO credentials when running existing commands.

## Rationale
AWS CLI v2 and AWS SSO use a completely new and different way to persist aws credentials.
This is likely to break compatability with a lot of existing tools that use AWS apis such as
terraform, awslogs and probably thousands more.

AWS Helper reads the "new and modern" credentials stored by aws cli v2, 
and extracts "old-school" environment variables from them. It then executes the specified command, within this environment.

## Prereqs:
- awshelper requires python 3.x (tested on 3.8) and pip
- aws cli v2 installed (make sure you run a recent build)
- your org is set up with AWS SSO so that you can run `aws configure sso`
- make sure your aws cli is working by running `aws sts get-caller-identity --profile myprofile`
If all this works, you're good to go.

## How to use awshelper 
install it:   
`pip install awshelper` or `pip3 install awshelper` depending on your setup
you can either use env vars to specify your profile:
`AWS_PROFILE=mytest awshelper <command>` or
`awshelper --profile mytest <command>` or
`awshelper --profile=mytest <command>`.
In any case, a named profile IS required (at least for now)

If you're a fan of `awslogs` you can now run it using `awshelper`:
`AWS_PROFILE=mytest pipenv run awshelper awslogs groups --aws-region eu-central-1`

## Limitations
- awshelper streams stdout, but other output streams haven't been fully tested
- non-utf characters in the out stream might fail (not tested)
- a profile name IS needed - either specified using environment variables or parameters. If both are specified, the parameter "wins".