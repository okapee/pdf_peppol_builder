select bankCode, branchCode, bankName, branchName from peppol_builder.bank as bk inner join peppol_builder.branch as br on bk.bankCode = br.branchBankCode order by bankCode, branchCode;

select * from peppol_builder.bank;

select * from peppol_builder.branch;