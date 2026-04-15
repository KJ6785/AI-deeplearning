export function Footer() {
  return (
    <footer className="border-t py-12">
      <div className="container mx-auto px-4">
        <div className="flex flex-col md:flex-row justify-between items-center gap-8 text-center md:text-left">
          <div className="space-y-4">
            <h3 className="text-lg font-bold">ShopEasy</h3>
            <p className="text-sm text-muted-foreground max-w-xs">
              Polar.sh 기반의 간단하고 강력한 디지털 상점 솔루션
            </p>
          </div>
          <div className="text-sm text-muted-foreground">
            © {new Date().getFullYear()} ShopEasy. All rights reserved.
          </div>
        </div>
      </div>
    </footer>
  )
}
