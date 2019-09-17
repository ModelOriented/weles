args = commandArgs(trailingOnly=TRUE)

model = args[1]

model = readRDS(paste0("../../../V/Models/", model, "/model"))

print(model)
