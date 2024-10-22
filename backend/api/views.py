# api/views.py
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Loan, LoanType

@login_required
def apply_for_loan(request):
    if request.method == 'POST':
        loan_type_id = request.POST.get('loan_type')
        amount = request.POST.get('amount')

        # Fetch the loan type based on the loan_type_id
        loan_type = LoanType.objects.get(id=loan_type_id)

        # Create a new loan instance
        loan = Loan(
            user=request.user,
            loan_type=loan_type,
            amount=amount,
            interest_rate=loan_type.interest_rate,  # Assuming you want to take interest from the LoanType
            term_months=loan_type.term_months,      # Assuming you want to take term from the LoanType
        )

        loan.save()
        messages.success(request, 'Loan application submitted successfully.')
        return redirect('loan_application_success')  # Redirect to a success page or loan summary

    loan_types = LoanType.objects.all()  # Get all loan types to render in the form
    return render(request, 'apply_for_loan.html', {'loan_types': loan_types})
