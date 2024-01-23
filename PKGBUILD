pkgname=maneki-neko
pkgver=1.0
pkgrel=0
pkgdesc="StratOS's Welcome app"
arch=("any")
url="https://github.com/lugvitc/stratos-maneki-neko"
license=('GPL-v3')
depends=('bash'
	 'dialog'
	 'gnome-terminal'
	 'python-click'
	 'python-pyqt5'
	 'qt5-tools'
	 'qt5-wayland'
	 'python-pyqt5-sip'
	 'python-dotenv')
optdepends=()
source=("git+${url}.git")
sha1sums=('SKIP')

package() {
    cd stratos-"$pkgname"
    mkdir -p $pkgdir/usr/local/bin
    install -D -m755 ./main.py $pkgdir/usr/local/bin/$pkgname
}
