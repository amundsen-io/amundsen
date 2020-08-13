This guide documents how to organize Amundsen in your source control repository.

Amundsen allows for a lot of flexibility and configurability of deployment, through three principles:
1. Configuration is done via Python source files, not text files, allowing deeper customization.
2. Loaded configuration files are done via explicit hooks, meaning there is a defined interface and no need to fork existing files for deep customization.
3. Repositories are split to allow for different deployments.

This setup has pros and cons. It means that even simple Amundsen installation will require at least some custom code. However, it also means that even for highly customized installs, it should not require outright forking of the source.

This is a practical guide for deploying a lightly-modified Amundsen into production. It aims to cover 99% of installations, with customizations to the data integrations, front-end, and authorization.

This guide does not attempt the 1% of installs that require forking existing files inside Amundsen. Generally, we consider cases where that is necessary to be non-supported. If you try to add functionality and can't do it using the existing hooks, please open an issue! Even if your modification itself isn't appropriate to mainline, we're happy to consider adding an insertion point that will allow your modification to work without forking.

# git submodules

As described in the architecture, Amundsen is split into 5 services. Each service has its own git repo. The "main" `amundsen` repo is thus very light all it has is some documentation, docker deployment files, and [submodule](https://git-scm.com/book/en/v2/Git-Tools-Submodules) links to each service.

Thus, the suggested setup is to fork the main `amundsen`, but to *not* fork the individual service repositories. Note that your fork must be private, since you will have configuration files inside.

So the first step is to create a private fork of the public repo. The steps differ based on the repo host you use.

## GitHub

If you use GitHub to host your repos, you'll need to do some manual work since the GitHub UI doesn't support creating a [private fork of a public repo](https://gist.github.com/0xjac/85097472043b697ab57ba1b1c7530274).

First, [create a private repo in your GitHub account](https://help.github.com/articles/creating-a-new-repository/) named `amundsen`,  `amundsendatabuilder`.

```
git clone --bare git@github.com:lyft/amundsen.git
cd amundsen.git
git push --mirror git@github.com:your_git_username_or_organization/amundsen.git
cd ..
rm -rf amundsen.git
git clone git@github.com:your_git_username_or_organization/amundsen.git
cd amundsen
git remote add upstream git@github.com:lyft/amundsen.git
git remote set-url --push upstream DISABLED

git submodule init update --remote # TODO
```

