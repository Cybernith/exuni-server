
from django.conf.urls import url

from crm.views import ProductViewSummaryAPIView, RecommendedProductsAPIView
from products.exuni_admin.views import AdminProductApiView, AdminProductDetailView, ProductCreateUpdateAPIView, \
    ProductPriceUpdateAPIView
from products.lists.views import BrandListView, AvailListView, ProductPropertyListView, ProductGalleryListView, \
    ProductListView, CategoryListView, NoContentProductListView, AffiliateForSaleProductsListView
from products.shop.views import ShopProductListView, ShopProductDetailView, RelatedProductsApiView, \
    SimilarBrandProductsApiView, SimilarAvailProductsApiView, SimilarPropertiesProductsApiView, \
    SimilarCategoryProductsApiView, TopViewedShopProductsAPIView, CategoryTreeView, BrandShopListView
from products.views import BrandApiView, BrandDetailView, AvailApiView, AvailDetailView, ProductPropertyApiView, \
    ProductPropertyDetailView, CategoryApiView, CategoryDetailView, ProductApiView, ProductDetailView, \
    ProductGalleryApiView, ProductGalleryDetailView, GalleryOfProductApiView, BrandLogoUpdateView, \
    CategoryPictureUpdateView, ProductsStoreReceiptsView, ProductSimpleApiView, NoContentProductsView, \
    ProductContentDevelopmentDetailView, ProductPictureUpdateView, AffiliateProductAddBusinessView, \
    ProductPriceHistoryApiView

app_name = 'products'
urlpatterns = [
    url(r'^adminProductsAll$', AdminProductApiView.as_view(), name='adminProductView'),
    url(r'^adminProductGet/(?P<pk>[0-9]+)$', AdminProductDetailView.as_view(), name='adminProductDetailView'),
    url(r'^adminProductCreate$', ProductCreateUpdateAPIView.as_view(), name='product-create'),
    url(r'^adminProductUpdate/(?P<pk>[0-9]+)$', ProductCreateUpdateAPIView.as_view(), name='product-update'),

    url(r'^brand$', BrandApiView.as_view(), name='brandApiView'),
    url(r'^brand/(?P<pk>[0-9]+)$', BrandDetailView.as_view(), name='brandDetailView'),
    url(r'^brand/all$', BrandListView.as_view(), name='brandListView'),
    url(r'^brandsLogoUpdate/(?P<pk>[0-9]+)$', BrandLogoUpdateView.as_view(), name='brandLogoUpdateView'),

    url(r'^avail$', AvailApiView.as_view(), name='availApiView'),
    url(r'^avail/(?P<pk>[0-9]+)$', AvailDetailView.as_view(), name='availDetailView'),
    url(r'^avail/all$', AvailListView.as_view(), name='availListView'),

    url(r'^productProperty$', ProductPropertyApiView.as_view(), name='productPropertyApiView'),
    url(r'^productProperty/(?P<pk>[0-9]+)$', ProductPropertyDetailView.as_view(), name='productPropertyDetailView'),
    url(r'^productProperty/all$', ProductPropertyListView.as_view(), name='productPropertyListView'),

    url(r'^category$', CategoryApiView.as_view(), name='categoryApiView'),
    url(r'^category/(?P<pk>[0-9]+)$', CategoryDetailView.as_view(), name='categoryDetailView'),
    url(r'^category/all$', CategoryListView.as_view(), name='categoryListView'),
    url(r'^categoryPictureUpdate/(?P<pk>[0-9]+)$', CategoryPictureUpdateView.as_view(),
        name='categoryPictureUpdateView'),

    url(r'^product$', ProductApiView.as_view(), name='productApiView'),
    url(r'^contentDevelopment/(?P<pk>[0-9]+)/$',
        ProductContentDevelopmentDetailView.as_view(), name='productApiView'),
    url(r'^allProduct$', ProductSimpleApiView.as_view(), name='productSimpleApiView'),
    url(r'^product/(?P<pk>[0-9]+)/$', ProductDetailView.as_view(), name='productDetailView'),
    url(r'^product/all$', ProductListView.as_view(), name='productListView'),
    url(r'^affiliateForSaleProducts$', AffiliateForSaleProductsListView.as_view(),
        name='affiliateForSaleProductsListView'),
    url(r'^affiliateProductAddBusiness$', AffiliateProductAddBusinessView.as_view(),
        name='affiliateProductAddBusinessView'),
    url(r'^product/noContent$', NoContentProductListView.as_view(), name='noContentProductListView'),
    url(r'^product/storeReceipts/(?P<pk>[0-9]+)$', ProductsStoreReceiptsView.as_view(), name='productsStoreReceiptsView'),
    url(r'^productPictureUpdate/(?P<pk>[0-9]+)$', ProductPictureUpdateView.as_view(),
        name='productPictureUpdateView'),

    url(r'^productGallery$', ProductGalleryApiView.as_view(), name='productGalleryApiView'),
    url(r'^productGallery/(?P<pk>[0-9]+)$', ProductGalleryDetailView.as_view(), name='productGalleryDetailView'),
    url(r'^productGallery/all$', ProductGalleryListView.as_view(), name='productGalleryListView'),

    url(r'^galleryOfProduct/(?P<pk>[0-9]+)$', GalleryOfProductApiView.as_view(), name='galleryOfProductApiView'),

    url(r'^productPriceHistory/(?P<order_id>[0-9]+)$', ProductPriceHistoryApiView.as_view(),
        name='productPriceHistory'),


    # shop APIs

    url(r'^product/shop$', ShopProductListView.as_view(), name='shopProductList'),
    url(r'^product/shop/detail/(?P<id>[0-9]+)$', ShopProductDetailView.as_view(), name='productDetail'),

    url(r'^product/(?P<product_id>[0-9]+)/related$', RelatedProductsApiView.as_view(), name='relatedProducts'),
    url(r'^product/(?P<product_id>[0-9]+)/similarBrand$', SimilarBrandProductsApiView.as_view(),
        name='similarBrandProducts'),
    url(r'^product/(?P<product_id>[0-9]+)/similarAvails$', SimilarAvailProductsApiView.as_view(),
        name='similarBrandProducts'),
    url(r'^product/(?P<product_id>[0-9]+)/similarProperties$', SimilarPropertiesProductsApiView.as_view(),
        name='similarPropertiesProduct'),
    url(r'^product/(?P<product_id>[0-9]+)/similarCategory$', SimilarCategoryProductsApiView.as_view(),
        name='similarCategoryProduct'),

    url(r'^product/topViewed$', TopViewedShopProductsAPIView.as_view(), name='shopProductList'),

    url(r'^product/(?P<product_id>[0-9]+)/viewSummary$', ProductViewSummaryAPIView.as_view(),
        name='productViewSummary'),

    url(r'^userRecommendation$', RecommendedProductsAPIView.as_view(),
        name='userRecommendation'),

    url(r'^categoryTree$', CategoryTreeView.as_view(),
        name='categoryTree'),

    url(r'^shopBrand$', BrandShopListView.as_view(),
        name='brandShop'),
    url(r'^changeProductPrice/(?P<product_id>[0-9]+)$', ProductPriceUpdateAPIView.as_view(), name='changeProductPrice'),

]
