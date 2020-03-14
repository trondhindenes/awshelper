# AWS Helper

<https://pypi.org/project/awshelper/>   
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
`pip install awshelper` or `pip3 install awshelper` depending on your setup. 
You should use a root/sudo user to install it globally

you can either use env vars to specify your profile:
`AWS_PROFILE=mytest awshelper <command>` or   
`awshelper --profile mytest <command>` or   
`awshelper --profile=mytest <command>`.   
In any case, a named profile IS required (at least for now)

If you're a fan of `awslogs` you can now run it using `awshelper`:   
`AWS_PROFILE=mytest awshelper awslogs groups --aws-region eu-central-1`     
...or `eksctl`:   
`AWS_PROFILE=mytest awshelper eksctl create cluster -f eksfargate.yml`   

## Limitations
- awshelper streams stdout, but other output streams haven't been fully tested
- non-utf characters in the out stream might fail (not tested)
- an AWS profile name IS needed - either specified using environment variables or parameters. If both are specified, the parameter "wins".
- it will only work with profiles configured with `aws configure sso`. If you point to a profile with regular access key/secret, it won't work.
- awshelper does not (yet) respect the "wrapped" command's exit code. It will always exit 0 as long as it is able to retrieve an aws credential. This may not e what you want, and is on the list of things to fix.

## Test using docker:
`docker run -it -v ~/.aws:/root/.aws:ro ubuntu`
then run
```
apt-get update && apt-get install python3-pip
pip3 install awshelper 
AWS_PROFILE=mytest awshelper <my command>
```
