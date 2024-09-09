pkgname=maneki-neko
pkgver=1.0
pkgrel=1
pkgdesc="StratOS's Welcome app"
arch=("any")
url="https://github.com/stratos-linux/stratos-maneki-neko"
license=('GPL-v3')
depends=('bash'
	 'dialog'
	 'gnome-terminal'
     'python'
     'python-pyqt5'
	 'qt5-wayland')
optdepends=()
source=("git+${url}")
sha1sums=('SKIP')

package() {
    echo "Haha"
    cd stratos-maneki-neko
    echo "hoho"
    mkdir -p $pkgdir/usr/local/bin
    install -D -m755 ./main.py $pkgdir/usr/local/bin/$pkgname
}
