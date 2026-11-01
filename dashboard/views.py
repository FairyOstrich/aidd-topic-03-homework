from django.db.models import DecimalField, ExpressionWrapper, F
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views.generic import CreateView, DeleteView, ListView, View, UpdateView

from .forms import PositionModelForm, ShareModelForm
from .models import Position, Share
from .services.graph import get_graph
from django.contrib.auth.mixins import UserPassesTestMixin


class IsUserAuthenticatedMixin(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_authenticated

    @staticmethod
    def handle_no_permission():
        return redirect("dashboard:index")


class ShareListView(ListView):
    """Список акций"""

    model = Share
    template_name = "dashboard/list.html"
    paginate_by = 100
    ordering = ["name"]


class ShareDetailView(View):
    @staticmethod
    def get(request, pk):
        share = Share.objects.get(id=pk)

        return render(
            request,
            "dashboard/detail.html",
            {"plot_div": get_graph(share), "share": share},
        )


class ShareCreateView(IsUserAuthenticatedMixin, CreateView):
    """Добавление инструмента"""

    template_name = "dashboard/create.html"
    form_class = ShareModelForm
    success_url = reverse_lazy("dashboard:index")


class ShareUpdateView(IsUserAuthenticatedMixin, UpdateView):
    """Редактирование инструмента"""

    model = Share
    template_name = "dashboard/create.html"
    form_class = ShareModelForm
    success_url = reverse_lazy("dashboard:index")


class ShareDeleteView(IsUserAuthenticatedMixin, DeleteView):
    """Удаление задачи"""

    model = Share
    template_name = "dashboard/delete.html"
    success_url = reverse_lazy("dashboard:index")


class PositionListView(IsUserAuthenticatedMixin, ListView):
    """Список позиций пользователя"""

    model = Position
    template_name = "dashboard/portfolio/list.html"
    context_object_name = "positions"

    def get_queryset(self):
        return (
            Position.objects.filter(user=self.request.user)
            .select_related("share")
            .annotate(
                current_value=ExpressionWrapper(
                    F("quantity") * F("share__last_price"),
                    output_field=DecimalField(max_digits=12, decimal_places=2),
                ),
                purchase_total=ExpressionWrapper(
                    F("quantity") * F("purchase_price"),
                    output_field=DecimalField(max_digits=12, decimal_places=2),
                ),
            )
            .annotate(
                profit=ExpressionWrapper(
                    F("current_value") - F("purchase_total"),
                    output_field=DecimalField(max_digits=12, decimal_places=2),
                ),
                profit_percent=ExpressionWrapper(
                    (F("profit") / F("purchase_total")) * 100,
                    output_field=DecimalField(max_digits=12, decimal_places=2),
                ),
            )
        )


class PositionCreateView(IsUserAuthenticatedMixin, CreateView):
    """Добавление позиции"""

    model = Position
    form_class = PositionModelForm
    template_name = "dashboard/portfolio/form.html"
    success_url = reverse_lazy("dashboard:portfolio")

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)


class PositionUpdateView(IsUserAuthenticatedMixin, UpdateView):
    """Редактирование позиции"""

    model = Position
    form_class = PositionModelForm
    template_name = "dashboard/portfolio/form.html"
    success_url = reverse_lazy("dashboard:portfolio")

    def get_queryset(self):
        return Position.objects.filter(user=self.request.user)


class PositionDeleteView(IsUserAuthenticatedMixin, DeleteView):
    """Удаление позиции"""

    model = Position
    template_name = "dashboard/portfolio/confirm_delete.html"
    success_url = reverse_lazy("dashboard:portfolio")

    def get_queryset(self):
        return Position.objects.filter(user=self.request.user)
