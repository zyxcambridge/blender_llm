#!/bin/bash

# 确保脚本在出错时停止
set -e

# 创建一个临时目录来存储 GitHub Pages 文件
echo "Creating temporary directory..."
mkdir -p gh-pages-temp
cp -r index.html styles.css images videos .nojekyll 404.html robots.txt sitemap.xml favicon.ico gh-pages-temp/
# 如果您有自定义域名，取消下面这行的注释并重命名文件
# cp CNAME.example gh-pages-temp/CNAME

# 进入临时目录
cd gh-pages-temp

# 初始化一个新的 git 仓库
echo "Initializing git repository..."
git init
git add .
git commit -m "Update GitHub Pages"

# 添加远程仓库
echo "Adding remote repository..."
git remote add origin https://github.com/zyxcambridge/blender_llm.git

# 推送到 gh-pages 分支
echo "Pushing to gh-pages branch..."
git push -f origin main:gh-pages

# 返回上一级目录并清理
cd ..
rm -rf gh-pages-temp

echo "Deployment complete! Your site should be available at https://zyxcambridge.github.io/blender_llm/"
