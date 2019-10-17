args <- commandArgs(trailingOnly = TRUE)

X = read.csv(args[3])[,2:65]
y = read.csv(args[4])[,2]

suppressMessages(library(DALEXtra))
suppressMessages(library(DALEX))
explain_scikitlearn(path = args[1], env = args[2],
                    data = X, y = y, verbose=F) -> explainer
if(length(args)==5) {
  print(explainer[[args[5]]])
} else {
  print(explainer)
}
