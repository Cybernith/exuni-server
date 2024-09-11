from django.conf.urls import url

from products.lists.views import BrandListView, AvailListView, ProductPropertyListView, ProductGalleryListView, \
    ProductListView, CategoryListView
from products.views import BrandApiView, BrandDetailView, AvailApiView, AvailDetailView, ProductPropertyApiView, \
    ProductPropertyDetailView, CategoryApiView, CategoryDetailView, ProductApiView, ProductDetailView, \
    ProductGalleryApiView, ProductGalleryDetailView, GalleryOfProductApiView, BrandLogoUpdateView, \
    CategoryPictureUpdateView

app_name = 'products'
urlpatterns = [
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
    url(r'^product/(?P<pk>[0-9]+)$', ProductDetailView.as_view(), name='productDetailView'),
    url(r'^product/all$', ProductListView.as_view(), name='productListView'),

    url(r'^productGallery$', ProductGalleryApiView.as_view(), name='productGalleryApiView'),
    url(r'^productGallery/(?P<pk>[0-9]+)$', ProductGalleryDetailView.as_view(), name='productGalleryDetailView'),
    url(r'^productGallery/all$', ProductGalleryListView.as_view(), name='productGalleryListView'),

    url(r'^galleryOfProduct/(?P<pk>[0-9]+)$', GalleryOfProductApiView.as_view(), name='galleryOfProductApiView'),

]
