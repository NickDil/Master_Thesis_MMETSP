library(shiny)
require('RMySQL')
require('rjson')
config <- fromJSON(file="/home/nidil/Drives/nidil/Documents/Project_TRAPID/Scripts/config.json")

mydb = dbConnect(MySQL(), user=config$username, password=config$pswd, dbname=config$db, host=config$urlDB)
dbListTables(mydb)
SQLstatement = "SELECT experiment_id, title from experiments where user_id = {user_id} AND description LIKE '%{query}%'"
counttr = "SELECT experiment_id, COUNT(experiment_id) FROM transcripts WHERE experiment_id IN {} GROUP BY experiment_id"
rs = dbSendQuery(mydb, "select * from experiments where user_id = 10")



# Define UI for app that draws a histogram ----
ui <- fluidPage(
  
  # App title ----
  titlePanel("Hello World!"),
  
  # Sidebar layout with input and output definitions ----
  sidebarLayout(
    
    # Sidebar panel for inputs ----
    sidebarPanel(
      
      # Input: Slider for the number of bins ----
      sliderInput(inputId = "bins",
                  label = "Number of bins:",
                  min = 1,
                  max = 150,
                  value = 30)
      
    ),
    
    # Main panel for displaying outputs ----
    mainPanel(
      
      # Output: Histogram ----
      plotOutput(outputId = "distPlot")
      
    )
  )
)
# Define server logic required to draw a histogram ----
server <- function(input, output) {
  
  # Histogram of the Old Faithful Geyser Data ----
  # with requested number of bins
  # This expression that generates a histogram is wrapped in a call
  # to renderPlot to indicate that:
  #
  # 1. It is "reactive" and therefore should be automatically
  #    re-executed when inputs (input$bins) change
  # 2. Its output type is a plot
  output$distPlot <- renderPlot({
    
    x    <- faithful$waiting
    bins <- seq(min(x), max(x), length.out = input$bins + 1)
    
    hist(x, breaks = bins, col = "#75AADB", border = "white",
         xlab = "Waiting time to next eruption (in mins)",
         main = "Histogram of waiting times")
    
  })
  
}
shinyApp(ui = ui, server = server)